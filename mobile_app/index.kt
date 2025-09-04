package com.example

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import retrofit2.*
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*

data class User(val id: Int, val name: String, val age: Int)

interface ApiService {
    @GET("users")
    fun getUsers(): Call<List<User>>

    @POST("users")
    fun addUser(@Body user: User): Call<User>
}

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val retrofit = Retrofit.Builder()
            .baseUrl("https://your-superhosting-api.com/api/") // Replace with your API base URL
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val api = retrofit.create(ApiService::class.java)

        // Get users
        api.getUsers().enqueue(object : Callback<List<User>> {
            override fun onResponse(call: Call<List<User>>, response: Response<List<User>>) {
                val users = response.body()
                println(users)
            }
            override fun onFailure(call: Call<List<User>>, t: Throwable) {
                println("Error: ${t.message}")
            }
        })

        // Add user
        val newUser = User(0, "Alice", 30)
        api.addUser(newUser).enqueue(object : Callback<User> {
            override fun onResponse(call: Call<User>, response: Response<User>) {
                println("User added: ${response.body()}")
            }
            override fun onFailure(call: Call<User>, t: Throwable) {
                println("Error: ${t.message}")
            }
        })
    }
}